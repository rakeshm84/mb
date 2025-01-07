import React, { useRef } from "react";
import { Editor } from "@tinymce/tinymce-react";
import PropTypes from "prop-types";

const TinyMCE = ({
  tinymceScriptSrc,
  onInit,
  initialValue,
  height,
  menubar,
  plugins,
  toolbar1,
  toolbar2,
  contentStyle = "body { font-family:Helvetica,Arial,sans-serif; font-size:14px }",
}) => {
  const editorRef = useRef(null);

  return (
    <Editor
      tinymceScriptSrc={tinymceScriptSrc}
      onInit={(evt, editor) => {
        editorRef.current = editor;
        if (onInit) onInit(evt, editor);
      }}
      initialValue={initialValue}
      init={{
        height,
        menubar,
        plugins,
        toolbar1,
        toolbar2,
        content_style: contentStyle,
      }}
    />
  );
};

TinyMCE.propTypes = {
  tinymceScriptSrc: PropTypes.string, // Path to the TinyMCE script file
  onInit: PropTypes.func, // Callback function for when the editor is initialized
  initialValue: PropTypes.string, // Initial content for the editor
  height: PropTypes.number, // Height of the editor in pixels
  menubar: PropTypes.bool, // Whether the menubar is displayed
  plugins: PropTypes.arrayOf(PropTypes.string), // List of plugins to include
  toolbar1: PropTypes.string, // Toolbar configuration
  toolbar2: PropTypes.string, // Toolbar configuration
  contentStyle: PropTypes.string, // Custom CSS for the editor's content
};

TinyMCE.defaultProps = {
  tinymceScriptSrc: process.env.REACT_APP_PUBLIC_URL + "/tinymce/tinymce.min.js",
  onInit: () => {},
  initialValue: "",
  height: 300,
  menubar: false,
  plugins: [
    "advlist",
    "autolink",
    "lists",
    "link",
    "image",
    "charmap",
    "preview",
    "anchor",
    "searchreplace",
    "visualblocks",
    "code",
    "fullscreen",
    "insertdatetime",
    "media",
    "table",
    "wordcount",
  ],
  toolbar1: `undo redo | formatselect | bold strikethrough italic underline | alignleft aligncenter alignright alignjustify | bullist numlist outdent indent | link unlink anchor | pastetext | image`,
  toolbar2: `print preview code | fontsizeselect | forecolor backcolor | styleselect fontselect fontsizeselect | hr removeformat charmap | insertdatetime`,
  contentStyle: "body { font-family:Helvetica,Arial,sans-serif; font-size:14px }",
};

export default TinyMCE;
